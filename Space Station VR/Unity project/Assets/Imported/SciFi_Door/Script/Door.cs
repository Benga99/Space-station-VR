using UnityEngine;
using System.Collections;

public class Door : MonoBehaviour {
	private Animator anim;

	private AudioSource audioS;
	public HovercarAnim hovercar;
	private StartMessage startMessageScript;

	bool floatingCar = false;

	public void Start()
	{
		GameObject door = GameObject.FindWithTag("SF_Door");
		anim = door.GetComponent<Animator>();
		audioS = this.GetComponent<AudioSource>();
		//hovercar = FindObjectOfType<HovercarAnim>();
		startMessageScript = FindObjectOfType<StartMessage>();
	}

	void OnTriggerEnter(Collider other)
	{
		if(other.gameObject.tag == "KeyCard" && enabled)
        {
			anim.SetBool("open", true);
			audioS.Play();
            if (!floatingCar)
            {
				floatingCar = true;
				hovercar.gameObject.SetActive(true);
				StartCoroutine(hovercar.Floating());
				//go to the car and leave

				//TODO STEAM
				//startMessageScript.onFinishEscapeRoom();
			}
			
		}
			

	}
	void OnTriggerExit(Collider other)
	{
		if(other.gameObject.tag == "KeyCard" && enabled)
        {
			anim.SetBool("open", false);
			audioS.Play();
		}
			
	}
}
