using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Valve.VR.Extras;
using UnityEngine.UI;
using UnityEngine.SceneManagement;

public class HintsManagerCanvas : MonoBehaviour
{
    [Header("Lasers")]
    public SteamVR_LaserPointer laserPointerRight;
    public SteamVR_LaserPointer laserPointerLeft;

    [Header("Buttons")]
    public GameObject hintButton;
    public GameObject restartButton;
    public GameObject leaveButton;

    [Header("Player")]
    public GameObject player;
    public List<GameObject> hints;

    private float timer = 0;
    private int hintIndex = 0;

    private Vector3 finalPosition = new Vector3(0f, 0f, 0.32f);
    private Vector3 finalRotation = new Vector3(0, 90, 0);

    private Color transparentColor = new Color(0, 0, 0, 0);

    void Awake()
    {
        laserPointerRight.PointerIn += PointerInside;
        laserPointerRight.PointerOut += PointerOutside;
        laserPointerRight.PointerClick += PointerClick;

        laserPointerLeft.PointerIn += PointerInside;
        laserPointerLeft.PointerOut += PointerOutside;
        laserPointerLeft.PointerClick += PointerClick;

        laserPointerLeft.active = false;
        laserPointerRight.active = false;
    }

    private void Update()
    {
        timer += Time.deltaTime;
        if (timer > 60 && hintIndex < 6)
        {
            hintButton.GetComponent<Button>().interactable = true;
            hintButton.GetComponent<BoxCollider>().size = new Vector3(400, 120, 50);
        }
    }

    public void PointerClick(object sender, PointerEventArgs e)
    {
        if (!e.target.CompareTag("UI")) { return; }

        if (e.target.name == "CanvasHints")
        {

        }
        else if (e.target.name == "HintButton")
        {
            if (timer > 60 && hintIndex < 6)
            {
                timer = 0;

                hintButton.GetComponent<Button>().interactable = false;
                hintButton.GetComponent<BoxCollider>().size = Vector3.zero;

                //activate hint

                StartCoroutine(showCard(hints[hintIndex]));
                hintIndex++;

                Debug.Log("hint used");
            }
        }
        else if (e.target.name == "RestartButton")
        {
            Destroy(player);
            SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex);
        }
        else if (e.target.name == "LeaveButton")
        {
            Destroy(player);
            SceneManager.LoadScene(0);
        }

    }

    public void PointerInside(object sender, PointerEventArgs e)
    {
        if (!e.target.CompareTag("UI")) { return; }

        if (e.target.name == "CanvasHints")
        {
            activateLasers();
        }
        else if (e.target.name == "HintButton")
        {
            activateLasers();
            if (timer > 60 && hintIndex < 6)
            {
                hintButton.GetComponent<Image>().color = Color.green;
            }
        }
        else if (e.target.name == "RestartButton")
        {
            activateLasers();
            restartButton.GetComponent<Image>().color = Color.green;
        }
        else if (e.target.name == "LeaveButton")
        {
            activateLasers();
            leaveButton.GetComponent<Image>().color = Color.green;
        }

    }

    public void PointerOutside(object sender, PointerEventArgs e)
    {
        if (!e.target.CompareTag("UI")) { return; }

        if (e.target.name == "CanvasHints")
        {
            deactivateLasers();
            Debug.Log("out of canvas");
        }
        else if (e.target.name == "HintButton")
        {
            hintButton.GetComponent<Image>().color = Color.white;
        }
        else if (e.target.name == "RestartButton")
        {
            restartButton.GetComponent<Image>().color = Color.white;
        }
        else if (e.target.name == "LeaveButton")
        {
            leaveButton.GetComponent<Image>().color = Color.white;
        }

    }

    private void activateLasers()
    {
        laserPointerLeft.thickness = 0.002f;
        laserPointerRight.thickness = 0.002f;

        laserPointerLeft.color = Color.black;
        laserPointerRight.color = Color.black;

        laserPointerLeft.clickColor = Color.green;
        laserPointerRight.clickColor = Color.green;
    }

    private void deactivateLasers()
    {
        laserPointerLeft.thickness = 0f;
        laserPointerRight.thickness = 0f;

        laserPointerLeft.color = transparentColor;
        laserPointerRight.color = transparentColor;

        laserPointerLeft.clickColor = transparentColor;
        laserPointerRight.clickColor = transparentColor;
    }

    IEnumerator showCard(GameObject card)
    {
        card.SetActive(true);
        card.transform.localScale = new Vector3(0.3333f, 0.01f, 0.3333f);
        card.transform.LeanMoveLocal(finalPosition, 2f).setEaseInOutCubic();
        yield return new WaitForSeconds(1.5f);


        while (card.transform.localEulerAngles.y % 181 < 180)
        {
            card.transform.Rotate(0, 3, 0);
            yield return new WaitForEndOfFrame();
        }
        card.transform.LeanScaleY(0.3333f, 1f).setEaseInOutBounce();
        yield return new WaitForSeconds(2f);
        Debug.Log("Canceled");
        LeanTween.cancel(this.gameObject);
    }
}
